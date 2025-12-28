import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { LogConfig } from '../schemas/log.schema';

@Injectable()
export class LogConfigService {
  constructor(private configService: ConfigService) {}

  get config(): LogConfig {
    return this.configService.get<LogConfig>('log')!;
  }

  get level(): string {
    return this.config.level;
  }

  get pretty(): boolean {
    return this.config.pretty;
  }

  get directory(): string {
    return this.config.directory;
  }

  get maxFiles(): number {
    return this.config.maxFiles;
  }

  get maxSize(): string {
    return this.config.maxSize;
  }

  shouldPrettyPrint(): boolean {
    return this.pretty && this.configService.get('nodeEnv') !== 'production';
  }

  getLogFilePath(filename: string): string {
    return `${this.directory}/${filename}`;
  }
}
