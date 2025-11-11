import { ClassSerializerInterceptor, ValidationPipe } from '@nestjs/common';
import { NestFactory, Reflector } from '@nestjs/core';
import { ConfigService } from '@nestjs/config';
import compression from 'compression';
import helmet from 'helmet';
import { AppModule } from './app.module';
import { setupWinstonLogger } from './infrastructure/logging/winston.logger';
import { setupGlobalFilters } from './common/filters/setup-filters';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: setupWinstonLogger(),
  });

  const config = app.get(ConfigService);
  const reflector = app.get(Reflector);

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  app.useGlobalInterceptors(new ClassSerializerInterceptor(reflector));

  setupGlobalFilters(app);

  app.enableCors({
    origin: config.get<string[]>('app.corsOrigins'),
    credentials: true,
  });

  app.use(helmet());
  app.use(compression());

  const globalPrefix = config.get<string>('app.globalPrefix');
  if (globalPrefix) {
    app.setGlobalPrefix(globalPrefix);
  }

  if (config.get<boolean>('app.enableVersioning')) {
    // Use URI versioning as a sane default
    // Example: /v1/...
  }

  const port = config.get<number>('app.port') ?? 3000;
  await app.listen(port);
}
bootstrap();
