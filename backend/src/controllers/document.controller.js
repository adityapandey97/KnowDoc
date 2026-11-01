import { documentService } from '../services/document.service.js';
import { ApiError } from '../utils/apiError.js';

export const documentController = {
  async upload(req, res, next) {
    try {
      if (!req.file) {
        throw ApiError.badRequest('No document file was uploaded.');
      }

      const document = await documentService.uploadDocument({
        userId: req.user.id,
        fileBuffer: req.file.buffer,
        originalFilename: req.file.originalname,
        mimeType: req.file.mimetype
      });

      res.status(202).json({
        success: true,
        data: {
          id: document._id.toString(),
          filename: document.originalFilename,
          status: document.status,
          sizeBytes: document.sizeBytes,
          fileHash: document.fileHash,
          createdAt: document.createdAt
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async list(req, res, next) {
    try {
      const result = await documentService.listDocuments(req.user.id, req.query);
      res.status(200).json({
        success: true,
        data: result.data.map((doc) => ({
          id: doc._id.toString(),
          filename: doc.originalFilename,
          status: doc.status,
          sizeBytes: doc.sizeBytes,
          pageCount: doc.pageCount,
          chunkCount: doc.chunkCount,
          createdAt: doc.createdAt,
          updatedAt: doc.updatedAt
        })),
        pagination: {
          page: result.page,
          limit: result.limit,
          total: result.total,
          totalPages: result.totalPages,
          hasMore: result.page < result.totalPages
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async getById(req, res, next) {
    try {
      const doc = await documentService.getDocumentById(req.user.id, req.params.id);
      res.status(200).json({
        success: true,
        data: {
          id: doc._id.toString(),
          filename: doc.originalFilename,
          status: doc.status,
          sizeBytes: doc.sizeBytes,
          pageCount: doc.pageCount,
          chunkCount: doc.chunkCount,
          errorDetails: doc.errorDetails,
          createdAt: doc.createdAt,
          updatedAt: doc.updatedAt
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async delete(req, res, next) {
    try {
      const result = await documentService.deleteDocument(req.user.id, req.params.id);
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (err) {
      next(err);
    }
  }
};

