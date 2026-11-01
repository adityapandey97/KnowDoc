import { Router } from 'express';
import multer from 'multer';
import { documentController } from '../controllers/document.controller.js';
import { authenticate } from '../middleware/auth.middleware.js';
import { validate } from '../middleware/validate.middleware.js';
import { listDocumentsSchema, documentIdParamSchema } from '../validators/document.validator.js';
import { config } from '../config/env.js';

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: config.storage.maxFileSizeBytes
  }
});

const router = Router();

router.use(authenticate);

router.post('/', upload.single('file'), documentController.upload);
router.get('/', validate(listDocumentsSchema, 'query'), documentController.list);
router.get('/:id', validate(documentIdParamSchema, 'params'), documentController.getById);
router.delete('/:id', validate(documentIdParamSchema, 'params'), documentController.delete);

export default router;

