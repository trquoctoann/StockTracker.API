import { ClassSerializerInterceptor, ValidationPipe } from '@nestjs/common';
import { NestFactory, Reflector } from '@nestjs/core';
import compression from 'compression';
import helmet from 'helmet';
import { AppModule } from './app.module';
import { setupWinstonLogger } from './infrastructure/logging/winston.logger';
import { setupGlobalFilters } from './common/filters/setup-filters';
import { AppConfigService } from './config/services/app-config.service';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: setupWinstonLogger(),
  });

  const appConfig = app.get(AppConfigService);
  const reflector = app.get(Reflector);

  // Setup global pipes
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  // Setup global interceptors
  app.useGlobalInterceptors(new ClassSerializerInterceptor(reflector));

  // Setup global filters
  setupGlobalFilters(app);

  // Enable CORS
  app.enableCors({
    origin: appConfig.corsOrigins,
    credentials: true,
  });

  // Security middlewares
  app.use(helmet());
  app.use(compression());

  // Set global prefix
  if (appConfig.globalPrefix) {
    app.setGlobalPrefix(appConfig.globalPrefix);
  }

  // Enable versioning if configured
  if (appConfig.enableVersioning) {
    // Use URI versioning as a sane default
    // Example: /v1/...
  }

  // Start server - typed property
  await app.listen(appConfig.port);

  // Log startup info
  console.log(`🚀 Application is running on: ${appConfig.apiUrl}`);
  console.log(
    `📝 Environment: ${appConfig.isProduction() ? 'PRODUCTION' : 'DEVELOPMENT'}`,
  );
}

bootstrap().catch((err) => {
  console.error('❌ Bootstrap error:', err);
  process.exit(1);
});
