import { INestApplication } from '@nestjs/common';
import { GlobalHttpExceptionFilter } from './http-exception.filter';

export function setupGlobalFilters(app: INestApplication) {
  app.useGlobalFilters(new GlobalHttpExceptionFilter());
}
