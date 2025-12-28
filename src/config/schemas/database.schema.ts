import { z } from 'zod';

export const databaseConfigSchema = z.object({
  host: z.string().default('localhost'),
  port: z.coerce.number().int().positive().default(5432),
  username: z.string().min(1),
  password: z.string().min(1),
  database: z.string().min(1),
  ssl: z
    .string()
    .default('false')
    .transform((v) => v === 'true'),
  poolMin: z.coerce.number().int().nonnegative().default(2),
  poolMax: z.coerce.number().int().positive().default(10),
  connectionTimeout: z.coerce.number().int().positive().default(30000),
});

export type DatabaseConfig = z.infer<typeof databaseConfigSchema>;
