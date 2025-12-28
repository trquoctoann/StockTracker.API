import { z } from 'zod';

export const appConfigSchema = z.object({
  name: z.string().default('StockTracker.API'),
  host: z.string().default('0.0.0.0'),
  port: z.coerce.number().int().positive().default(3000),
  globalPrefix: z.string().default('api'),
  enableVersioning: z
    .string()
    .default('true')
    .transform((v) => v === 'true'),
  corsOrigins: z
    .string()
    .default('*')
    .transform((val) =>
      val
        .split(',')
        .map((x) => x.trim())
        .filter((x) => x.length > 0),
    ),
});

export type AppConfig = z.infer<typeof appConfigSchema>;
