import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { AppConfig } from '../schemas/app.schema';

@Injectable()
export class AppConfigService {
  constructor(private configService: ConfigService) {}

  get config(): AppConfig {
    return this.configService.get<AppConfig>('app')!;
  }

  get name(): string {
    return this.config.name;
  }

  get host(): string {
    return this.config.host;
  }

  get port(): number {
    return this.config.port;
  }

  get globalPrefix(): string {
    return this.config.globalPrefix;
  }

  get enableVersioning(): boolean {
    return this.config.enableVersioning;
  }

  get corsOrigins(): string[] {
    return this.config.corsOrigins;
  }

  get baseUrl(): string {
    return `http://${this.host}:${this.port}`;
  }

  get apiUrl(): string {
    return `${this.baseUrl}/${this.globalPrefix}`;
  }

  isProduction(): boolean {
    return this.configService.get('nodeEnv') === 'production';
  }

  isDevelopment(): boolean {
    return this.configService.get('nodeEnv') === 'development';
  }

  isTest(): boolean {
    return this.configService.get('nodeEnv') === 'test';
  }
}
