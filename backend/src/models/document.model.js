import mongoose from 'mongoose';

const documentSchema = new mongoose.Schema(
  {
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
      index: true
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
  },
  {
    timestamps: true
  }
);

documentSchema.index({ userId: 1, createdAt: -1 });
documentSchema.index({ userId: 1, fileHash: 1 });

export const Document = mongoose.model('Document', documentSchema);

