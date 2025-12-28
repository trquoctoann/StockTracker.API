import { Global, Module } from '@nestjs/common';
import { ConfigModule as NestConfigModule } from '@nestjs/config';
import configurationLoader from './configuration.loader';
import { validateEnv } from './schemas/env.schema';
import { AppConfigService } from './services/app-config.service';
import { LogConfigService } from './services/log-config.service';
import { DatabaseConfigService } from './services/database-config.service';

@Global()
@Module({
  imports: [
    NestConfigModule.forRoot({
      isGlobal: true,
      load: [configurationLoader],
      validate: validateEnv,
      expandVariables: true,
      envFilePath: [
        `.env.${process.env.NODE_ENV || 'development'}`,
        '.env',
      ].filter(Boolean),
      ignoreEnvFile: false,
    }),
  ],
  providers: [AppConfigService, LogConfigService, DatabaseConfigService],
  exports: [AppConfigService, LogConfigService, DatabaseConfigService],
})
export class ConfigModule {}
