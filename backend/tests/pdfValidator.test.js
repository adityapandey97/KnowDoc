import { validatePdfSignature } from '../src/utils/pdfValidator.js';
import { ApiError } from '../src/utils/apiError.js';

describe('PDF Validator Utility', () => {
  it('should accept a genuine PDF buffer with standard magic bytes', () => {
    // Standard PDF header '%PDF-1.7'
    const validPdfBuffer = Buffer.from('%PDF-1.7\n%âãÏÓ\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF');
    expect(() => validatePdfSignature(validPdfBuffer, 'application/pdf')).not.toThrow();
  });

  it('should reject a text or HTML file disguised as a PDF', () => {
    const fakePdfBuffer = Buffer.from('<html><body>Fake PDF payload</body></html>');
    expect(() => validatePdfSignature(fakePdfBuffer, 'application/pdf')).toThrow(ApiError);
  });

  it('should reject when MIME type is mismatched', () => {
    const validPdfBuffer = Buffer.from('%PDF-1.7\n%test');
    expect(() => validatePdfSignature(validPdfBuffer, 'image/png')).toThrow(ApiError);
  });

  it('should reject empty or undersized buffers', () => {
    const tinyBuffer = Buffer.from('%PDF');
    expect(() => validatePdfSignature(tinyBuffer, 'application/pdf')).toThrow(ApiError);
  });
});

