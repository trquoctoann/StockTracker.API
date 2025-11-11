import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { Request, Response } from 'express';

type HttpErrorBody = {
  statusCode?: number;
  message?: string | string[];
  error?: string;
  [key: string]: unknown;
};

@Catch()
export class GlobalHttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const isHttpException = exception instanceof HttpException;
    const status = isHttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;

    let normalizedMessage = 'Internal server error';
    let errorName = 'InternalServerError';

    if (isHttpException) {
      const body = exception.getResponse();
      const parsed: HttpErrorBody =
        typeof body === 'string' ? { message: body } : (body as HttpErrorBody);

      if (Array.isArray(parsed.message)) {
        normalizedMessage = parsed.message.join(', ');
      } else if (
        typeof parsed.message === 'string' &&
        parsed.message.length > 0
      ) {
        normalizedMessage = parsed.message;
      } else if (
        typeof exception.message === 'string' &&
        exception.message.length > 0
      ) {
        normalizedMessage = exception.message;
      }

      errorName = exception.name;
    }

    const payload = {
      success: false,
      statusCode: status,
      error: errorName,
      message: normalizedMessage,
      path: request.originalUrl,
      timestamp: new Date().toISOString(),
    };

    response.status(status).json(payload);
  }
}
