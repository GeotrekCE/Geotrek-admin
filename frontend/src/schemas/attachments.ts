import * as z from "zod"

export type AttachmentsSchemaProps = z.infer<typeof attachmentsSchema>

export const attachmentsSchema = z.object({
  attachments: z
    .array(z.object({ value: z.union([z.instanceof(File), z.null()]) }))
    .optional(),
})
