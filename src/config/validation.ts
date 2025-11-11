import { plainToInstance } from 'class-transformer';
import {
  IsBooleanString,
  IsNumber,
  IsOptional,
  IsString,
  validateSync,
} from 'class-validator';

class EnvironmentVariables {
  @IsOptional()
  @IsString()
  NODE_ENV?: string;

  @IsOptional()
  @IsString()
  APP_NAME?: string;

  @IsOptional()
  @IsString()
  HOST?: string;

  @IsOptional()
  @IsNumber()
  PORT?: number;

  @IsOptional()
  @IsString()
  GLOBAL_PREFIX?: string;

  @IsOptional()
  @IsBooleanString()
  API_VERSIONING?: string;

  @IsOptional()
  @IsString()
  CORS_ORIGINS?: string;

  @IsOptional()
  @IsString()
  LOG_LEVEL?: string;

  @IsOptional()
  @IsBooleanString()
  LOG_PRETTY?: string;
}

export function validateEnv(config: Record<string, unknown>) {
  const validated = plainToInstance(EnvironmentVariables, config, {
    enableImplicitConversion: true,
  });
  const errors = validateSync(validated, { skipMissingProperties: true });
  if (errors.length > 0) {
    throw new Error(`Config validation error: ${errors.toString()}`);
  }
  return validated;
}
