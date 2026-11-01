import { Router } from 'express';
import { conversationController } from '../controllers/conversation.controller.js';
import { authenticate } from '../middleware/auth.middleware.js';
import { validate } from '../middleware/validate.middleware.js';
import {
  createConversationSchema,
  sendMessageSchema,
  conversationIdParamSchema
} from '../validators/conversation.validator.js';

const router = Router();

router.use(authenticate);

router.post('/', validate(createConversationSchema), conversationController.create);
router.get('/', conversationController.list);
router.get('/:id', validate(conversationIdParamSchema, 'params'), conversationController.getById);
router.post(
  '/:id/messages',
  validate(conversationIdParamSchema, 'params'),
  validate(sendMessageSchema),
  conversationController.sendMessage
);

export default router;

