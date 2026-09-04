import * as React from "react"
import { createFileRoute, Link } from "@tanstack/react-router"
import Header from "@/components/header"
import { useAsyncStoredData } from "@/hook/useStoredData"
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import { Check, ChevronRight, X } from "lucide-react"
import { dateCompare, getDurationLabel } from "@/lib/date"
import { m } from "@/paraglide/messages"
import type {
  InfrastructureReferencesSchemaProps,
  InterventionReferencesSchemaProps,
  ReportReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import { Button } from "@/components/ui/button"
import useSyncDataMutations from "@/hook/useSyncDataMutations"
import { cn } from "@/lib/utils"
import { FetchError } from "@/lib/api"
import type {
  InfrastructureDataSchemaProps,
  InterventionDataSchemaProps,
  ReportDataSchemaProps,
  SignageDataSchemaProps,
} from "@/schemas/data"
import { Spinner } from "@/components/ui/spinner"
import { toast } from "sonner"
import useOnline from "@/hook/useOnline"

type ResultPromise =
  | string
  | SignageDataSchemaProps
  | InfrastructureDataSchemaProps
  | InterventionDataSchemaProps
  | ReportDataSchemaProps
  | FetchError

function getAttachmentErrors(result?: ResultPromise) {
  if (
    typeof result === "object" &&
    !("message" in result) &&
    "attachmentErrors" in result &&
    Array.isArray(result.attachmentErrors)
  ) {
    return result.attachmentErrors as string[]
  }

  return []
}

function getFailedAttachments(result?: ResultPromise) {
  if (
    typeof result === "object" &&
    !("message" in result) &&
    "failedAttachments" in result &&
    Array.isArray(result?.failedAttachments)
  ) {
    return result.failedAttachments as { value: File | null }[]
  }

  return []
}

function getStatusFromResult(result?: ResultPromise) {
  if (result === undefined) {
    return {
      isError: null,
      isSuccess: null,
    }
  }
  if (result instanceof Error) {
    const message =
      typeof result.res?.message === "string" ? result.res.message : "{}"

    return {
      isError: true,
      isSuccess: false,
      data: Object.entries(JSON.parse(message)).map(
        ([key, value]) =>
          `${key.replace("_id", "")} : ${Array.isArray(value) ? value.join(", ") : value}`
      ),
    }
  }
  return {
    isError: null,
    isSuccess: true,
    data: [result],
  }
}

export const Route = createFileRoute("/{-$locale}/_authenticated/sync/upload")({
  component: RouteComponent,
})

function RouteComponent() {
  const asyncData = useAsyncStoredData()
  const online = useOnline()

  const {
    signageMutation,
    interventionMutation,
    infrastructureMutation,
    reportMutation,
  } = useSyncDataMutations()

  const references = useLiveQuery(() =>
    db.references.bulkGet([
      "signage",
      "intervention",
      "infrastructure",
      "report",
    ])
  )
  const [signage, intervention, infrastructure, report] =
    (references as
      | [
          SignageReferencesSchemaProps,
          InterventionReferencesSchemaProps,
          InfrastructureReferencesSchemaProps,
          ReportReferencesSchemaProps,
        ]
      | undefined) || []

  const handleSubmit = React.useCallback(async () => {
    const [signageData, interventionData, infrastructureData, reportData] =
      asyncData ?? []
    const tableByReference = {
      signage: db.signageData,
      intervention: db.interventionData,
      infrastructure: db.infrastructureData,
      report: db.reportData,
    } as const
    const refByReference = {
      signage: "signage",
      intervention: "intervention",
      infrastructure: "infrastructure",
      report: "report",
    } as const

    const handleResult = (
      reference: keyof typeof tableByReference,
      result: Record<string, unknown>[],
      variables: Array<{ id?: number; appNewItem?: boolean }>
    ) => {
      result
        .flatMap((entry) => Object.values(entry))
        .forEach((value, index) => {
          const status = getStatusFromResult(value as ResultPromise)
          if (!status.isSuccess || !value || typeof value !== "object") {
            return
          }

          const targetId = variables[index]?.id
          if (targetId == null) {
            return
          }

          const failedAttachments = getFailedAttachments(value as ResultPromise)
          const nextValue =
            failedAttachments.length > 0
              ? {
                  ...value,
                  attachments: failedAttachments,
                  appSynced: false,
                }
              : value

          tableByReference[reference].where({ id: targetId }).delete()
          if (!variables[index].appNewItem && failedAttachments.length === 0) {
            db.rawData
              .where({ reference: refByReference[reference], id: targetId })
              .delete()
          }

          if (variables[index].appNewItem && failedAttachments.length > 0) {
            db.rawData.put({
              ...(value as
                | SignageDataSchemaProps
                | InterventionDataSchemaProps
                | InfrastructureDataSchemaProps
                | ReportDataSchemaProps),
              reference: refByReference[reference],
            })
          }
          tableByReference[reference].put(nextValue as never)

          toast.success(m["common.sync-up-success"](), {
            id: "upload-success",
            position: "top-center",
          })

          getAttachmentErrors(value as ResultPromise).forEach((error) =>
            toast.error(error, {
              id: `upload-attachment-error-${targetId}`,
              position: "top-center",
            })
          )
        })
    }

    if (signageData && signageData.length) {
      signageMutation.mutate(signageData, {
        onSuccess: (result, variables) =>
          handleResult(
            "signage",
            result as Record<string, unknown>[],
            variables
          ),
      })
    }
    if (interventionData && interventionData.length) {
      interventionMutation.mutate(interventionData, {
        onSuccess: (result, variables) =>
          handleResult(
            "intervention",
            result as Record<string, unknown>[],
            variables
          ),
      })
    }

    if (infrastructureData && infrastructureData.length) {
      infrastructureMutation.mutate(infrastructureData, {
        onSuccess: (result, variables) =>
          handleResult(
            "infrastructure",
            result as Record<string, unknown>[],
            variables
          ),
      })
    }

    if (reportData && reportData.length) {
      reportMutation.mutate(reportData, {
        onSuccess: (result, variables) =>
          handleResult(
            "report",
            result as Record<string, unknown>[],
            variables
          ),
      })
    }
  }, [
    asyncData,
    infrastructureMutation,
    interventionMutation,
    reportMutation,
    signageMutation,
  ])

  if (!asyncData) {
    return null // todo loading
  }
  const elements = asyncData
    .map((collection, index) => {
      // Signage
      if (index === 0) {
        return collection.map((item) => ({
          ...item,
          reference: "signage",
          pictogram: signage?.pictogram,
        }))
      }
      // Intervention
      if (index === 1) {
        return collection.map((item) => ({
          ...item,
          reference: "intervention",
          pictogram: intervention?.pictogram,
        }))
      }
      // Infrastructure
      if (index === 2) {
        return collection.map((item) => ({
          ...item,
          reference: "infrastructure",
          pictogram: infrastructure?.pictogram,
        }))
      }
      // Report
      if (index === 3) {
        return collection.map((item) => ({
          ...item,
          name: `Signalement (id: ${item.id})`,
          reference: "report",
          pictogram: report?.pictogram,
        }))
      }
    })
    .filter((item) => !!item)
    .flat()
    .sort((a, b) => dateCompare(b.date_update, a.date_update))

  const mutationList = {
    signage: signageMutation,
    intervention: interventionMutation,
    infrastructure: infrastructureMutation,
    report: reportMutation,
  }

  return (
    <div>
      <Header title="Éléments non synchronisés" withBackbutton />
      <section className="m-4">
        <ul>
          {elements.length === 0 && (
            <p className="py-4 text-center">{m["common.empty-state"]()}</p>
          )}
          {elements.map((item) => {
            const mutationItem =
              mutationList[item.reference as keyof typeof mutationList]

            const result = getStatusFromResult(
              mutationItem.data?.find(
                (mutationData) => !!mutationData?.[item.id]
              )?.[item.id]
            )

            const hasAttachmentErrors = result.data?.some(
              (item) => getAttachmentErrors(item as ResultPromise).length > 0
            )

            return (
              <li key={`${item.reference}-${item.id}`} className="my-4">
                <Item
                  variant="outline"
                  render={
                    <Link
                      to={`/{-$locale}/data/$type/$id`}
                      params={{
                        id: item.id.toString(),
                        type: item.reference,
                      }}
                      className={cn(
                        "bg-accent",
                        result.isSuccess &&
                          "border-green-600 [a]:hover:bg-green-600/10!",
                        (result.isError || hasAttachmentErrors) &&
                          "border-destructive bg-destructive/10 [a]:hover:bg-destructive/10!"
                      )}
                    >
                      {mutationItem.isPending && (
                        <ItemMedia>
                          <Spinner
                            role="img"
                            className="m-3 size-6"
                            aria-label={m["common.loading"]()}
                          />
                        </ItemMedia>
                      )}
                      {item.pictogram && !mutationItem.isPending && (
                        <ItemMedia>
                          <img loading="lazy" src={item.pictogram.url} alt="" />
                        </ItemMedia>
                      )}
                      <ItemContent>
                        <ItemTitle className="text-accent-foreground">
                          {/* @ts-expect-error report name */}
                          {item.name}
                        </ItemTitle>
                        <ItemDescription className="line-clamp-none">
                          {m[
                            `content.${item.reference as "signage" | "infrastructure" | "report" | "intervention"}`
                          ]()}
                          -{" "}
                          <time
                            dateTime={item.date_update}
                            className="text-xs text-muted-foreground"
                          >
                            {item.appNewItem === true
                              ? getDurationLabel(item.date_update, "created")
                              : getDurationLabel(item.date_update, "updated")}
                          </time>
                        </ItemDescription>
                        {result.isError && (
                          <div className="mt-3 text-accent-foreground">
                            <span className="flex items-center gap-2 font-bold">
                              <X className="size-4" aria-hidden />
                              {m["common.sync-error"]()}
                            </span>
                            <div className="ms-6">
                              {result.data.map((item) => (
                                <p key={item} className="my-1 text-sm">
                                  {item}
                                </p>
                              ))}
                            </div>
                          </div>
                        )}
                        {result.isSuccess && hasAttachmentErrors && (
                          <div className="mt-3 text-accent-foreground">
                            <span className="flex items-center gap-2 font-bold">
                              <X className="size-4" aria-hidden />
                              {m["common.sync-up-success-with-errors"]()}
                            </span>
                            <div className="ms-6">
                              {result.data.map((item, index) => (
                                <p key={index} className="my-1 text-sm">
                                  {getAttachmentErrors(
                                    item as ResultPromise
                                  ).join(", ")}
                                </p>
                              ))}
                            </div>
                          </div>
                        )}
                        {result.isSuccess && !hasAttachmentErrors && (
                          <div className="mt-3 text-accent-foreground">
                            <span className="flex items-center gap-2 font-bold">
                              <Check className="size-4" aria-hidden />
                              {m["common.sync-success"]()}
                            </span>
                          </div>
                        )}
                      </ItemContent>
                      <ItemActions>
                        <ChevronRight aria-hidden />
                      </ItemActions>
                    </Link>
                  }
                />
              </li>
            )
          })}
        </ul>
        {online ? (
          <Button className="w-full" onClick={handleSubmit}>
            {m["common.send-data"]()}
          </Button>
        ) : (
          <p className="text-center text-accent-foreground">
            {m["common.offline-cannot-sync"]()}
          </p>
        )}
      </section>
    </div>
  )
}
