import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { DatabaseConfig } from '../schemas/database.schema';

@Injectable()
export class DatabaseConfigService {
  constructor(private configService: ConfigService) {}

  get config(): DatabaseConfig {
    return this.configService.get<DatabaseConfig>('database')!;
  }

  get host(): string {
    return this.config.host;
  }

  get port(): number {
    return this.config.port;
  }

  get username(): string {
    return this.config.username;
  }

  get password(): string {
    return this.config.password;
  }

  get database(): string {
    return this.config.database;
  }

  get ssl(): boolean {
    return this.config.ssl;
  }

  get poolMin(): number {
    return this.config.poolMin;
  }

  get poolMax(): number {
    return this.config.poolMax;
  }

  get connectionTimeout(): number {
    return this.config.connectionTimeout;
  }

  getConnectionString(): string {
    const sslParam = this.ssl ? '?ssl=true' : '';
    return `postgresql://${this.username}:${this.password}@${this.host}:${this.port}/${this.database}${sslParam}`;
  }

  getConnectionOptions() {
    return {
      host: this.host,
      port: this.port,
      user: this.username,
      password: this.password,
      database: this.database,
      ssl: this.ssl,
      min: this.poolMin,
      max: this.poolMax,
      connectionTimeoutMillis: this.connectionTimeout,
    };
  }
}
