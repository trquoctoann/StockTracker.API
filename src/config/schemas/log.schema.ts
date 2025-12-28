import { z } from 'zod';

export const logConfigSchema = z.object({
  level: z.enum(['info', 'error', 'warn', 'debug']).default('info'),
  pretty: z
    .string()
    .default('true')
    .transform((v) => v === 'true'),
  directory: z.string().default('./logs'),
  maxFiles: z.coerce.number().int().positive().default(14),
  maxSize: z.string().default('20m'),
});

export type LogConfig = z.infer<typeof logConfigSchema>;
