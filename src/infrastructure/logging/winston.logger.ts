import { WinstonModule, utilities as nestWinstonUtilities } from 'nest-winston';
import { transports as winstonTransports } from 'winston';
import type { LoggerService } from '@nestjs/common';

export function setupWinstonLogger(): LoggerService {
  return WinstonModule.createLogger({
    transports: [
      new winstonTransports.Console({
        level: process.env.LOG_LEVEL ?? 'info',

        format: nestWinstonUtilities.format.nestLike('StockTracker.API', {
          colors: true,
          prettyPrint: true,
        }),
      }),
    ],
  });
}
