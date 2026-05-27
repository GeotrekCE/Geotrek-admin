import * as z from "zod"

export type CommonReferencesSchemaProps = z.infer<typeof commonReferencesSchema>
export type InfrastructureReferencesSchemaProps = z.infer<
  typeof infrastructureReferencesSchema
>
export type SignageReferencesSchemaProps = z.infer<
  typeof signageReferencesSchema
>

export type InterventionReferencesSchemaProps = z.infer<
  typeof interventionReferencesSchema
>
export type ReportReferencesSchemaProps = z.infer<typeof reportReferencesSchema>

export type ReferencesSchemapProps = {
  common: CommonReferencesSchemaProps
  infrastructure: InfrastructureReferencesSchemaProps
  signage: SignageReferencesSchemaProps
  intervention: InterventionReferencesSchemaProps
  report: ReportReferencesSchemaProps
}

export const commonReferencesSchema = z.object({
  structure: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  organism: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  accessmean: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
})

export const infrastructureReferencesSchema = z.object({
  infrastructuretype: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    })
  ),
  infrastructuremaintenancedifficultylevel: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  infrastructureusagedifficultylevel: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  infrastructurecondition: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  pictogram: z.object({
    url: z.string(),
  }),
})

export const signageReferencesSchema = z.object({
  signagecondition: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  signagetype: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    })
  ),
  sealing: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  direction: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  bladetype: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  color: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  bladecondition: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  pictogram: z.object({
    url: z.string(),
  }),
})

export const interventionReferencesSchema = z.object({
  contractor: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  interventiondisorder: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  stake: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  interventionstatus: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  interventiontype: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  interventionjob: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  pictogram: z.object({
    url: z.string(),
  }),
})

export const reportReferencesSchema = z.object({
  reportactivity: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  reportcategory: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  reportproblemmagnitude: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  reportstatus: z.array(z.unknown()),
  pictogram: z.object({
    url: z.string(),
  }),
})
