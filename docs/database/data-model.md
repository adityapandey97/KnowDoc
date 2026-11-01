# KnowDoc — Data Models & Schemas

## 1. Overview
KnowDoc employs a hybrid persistence model:
1. **MongoDB**: Stores semi-structured, state-heavy application entities (Users, Document Metadata, Conversations, Messages).
2. **PostgreSQL with pgvector**: Stores high-dimensional vector embeddings, text passages, and precision evaluation records.

---

## 2. MongoDB Document Models (Mongoose)

### 2.1 `User` Collection (`users`)
Stores tenant identity, credentials, and organizational metadata.

```javascript
const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true,
    index: true
  },
  passwordHash: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user'
  },
  isActive: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});
```

### 2.2 `Document` Collection (`documents`)
Stores document lifecycle states, storage references, cryptographic checksums, and parsing results.

```javascript
const documentSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  filename: {
    type: String,
    required: true
  },
  originalFilename: {
    type: String,
    required: true
  },
  storageKey: {
    type: String,
    required: true,
    unique: true
  },
  fileHash: {
    type: String,
    required: true,
    index: true // SHA-256 for duplicate detection
  },
  sizeBytes: {
    type: Number,
    required: true
  },
  mimeType: {
    type: String,
    required: true,
    default: 'application/pdf'
  },
  pageCount: {
    type: Number,
    default: 0
  },
  chunkCount: {
    type: Number,
    default: 0
  },
  status: {
    type: String,
    enum: ['pending', 'processing', 'chunked', 'embedding', 'ready', 'failed'],
    default: 'pending',
    index: true
  },
  isScanned: {
    type: Boolean,
    default: false
  },
  errorDetails: {
    code: { type: String },
    message: { type: String },
    failedAt: { type: Date }
  },
  metadata: {
    author: { type: String },
    title: { type: String },
    creationDate: { type: Date }
  }
}, {
  timestamps: true
});

// Compound index for user workspace listing
documentSchema.index({ userId: 1, createdAt: -1 });
// Compound index for user duplicate check
documentSchema.index({ userId: 1, fileHash: 1 });
```

### 2.3 `Conversation` Collection (`conversations`)
Maintains conversational threads bound to documents.

```javascript
const conversationSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  title: {
    type: String,
    required: true,
    default: 'New Conversation'
  },
  documentIds: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Document',
    required: true
  }],
  lastMessageAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

conversationSchema.index({ userId: 1, lastMessageAt: -1 });
```

### 2.4 `Message` Collection (`messages`)
Stores each turn in a conversation, including query, response, and citations.

```javascript
const messageSchema = new mongoose.Schema({
  conversationId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Conversation',
    required: true,
    index: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  role: {
    type: String,
    enum: ['user', 'assistant', 'system'],
    required: true
  },
  content: {
    type: String,
    required: true
  },
  citations: [{
    documentId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Document',
      required: true
    },
    documentName: { type: String },
    pageNumber: { type: Number, required: true },
    excerpt: { type: String, required: true },
    similarityScore: { type: Number }
  }],
  tokenUsage: {
    promptTokens: { type: Number },
    completionTokens: { type: Number },
    totalTokens: { type: Number }
  }
}, {
  timestamps: true
});

messageSchema.index({ conversationId: 1, createdAt: 1 });
```

---

## 3. PostgreSQL with pgvector Schemas

PostgreSQL manages the vector representation of text chunks. The schema is initialized with the `vector` extension.

### 3.1 DDL: `document_chunks` Table
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(1536), -- Configurable dimension (e.g. 1536 for OpenAI, 768 for BGE)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_doc_chunk UNIQUE (document_id, chunk_index)
);
```

### 3.2 DDL: `rag_evaluations` Table
Tracks retrieval accuracy metrics, ground truth feedback, and citation auditing.

```sql
CREATE TABLE IF NOT EXISTS rag_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(64) NOT NULL,
    message_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    query TEXT NOT NULL,
    retrieved_chunk_ids UUID[] NOT NULL,
    retrieval_latency_ms INTEGER NOT NULL,
    generation_latency_ms INTEGER NOT NULL,
    citation_precision_score FLOAT,
    user_rating SMALLINT, -- 1 (thumbs up) or -1 (thumbs down)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Cross-Datastore Mapping & Cleanup Strategy

### 4.1 ID Representation
- MongoDB `_id` is a 24-character hexadecimal BSON ObjectId string (e.g., `6543210987abcdef01234567`).
- In PostgreSQL, `document_id` and `user_id` are stored as `VARCHAR(64)` matching the exact string serialization.
- This decoupling prevents hard foreign key dependencies between distinct database clusters while providing fast B-Tree index lookup.

### 4.2 Cascading Deletion Protocol
When `DELETE /api/v1/documents/:id` is invoked:
1. **Verification**: Express confirms `document.userId == authUser.id`.
2. **PostgreSQL Deletion**:
   ```sql
   DELETE FROM document_chunks WHERE user_id = $1 AND document_id = $2;
   ```
3. **Storage Binary Deletion**:
   ```javascript
   await storageProvider.deleteObject(document.storageKey);
   ```
4. **MongoDB Document Record Deletion**:
   ```javascript
   await Document.deleteOne({ _id: documentId, userId });
   ```
5. **Reference Pruning**:
   ```javascript
   await Conversation.updateMany(
     { userId, documentIds: documentId },
     { $pull: { documentIds: documentId } }
   );
   ```

