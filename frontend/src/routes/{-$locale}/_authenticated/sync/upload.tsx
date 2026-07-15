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
import { getLocale } from "@/paraglide/runtime"
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

type ResultPromise =
  | string
  | SignageDataSchemaProps
  | InfrastructureDataSchemaProps
  | InterventionDataSchemaProps
  | ReportDataSchemaProps
  | FetchError

function getStatusFromResult(result?: ResultPromise) {
  if (result === undefined) {
    return {
      isError: null,
      isSuccess: null,
    }
  }
  if (result instanceof FetchError) {
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

    if (signageData && signageData.length) {
      signageMutation.mutate(signageData, {
        onSuccess(result, variables) {
          result
            .flatMap((item) => Object.values(item))
            .map(getStatusFromResult)
            .map(({ data, isSuccess }, index) => {
              if (isSuccess) {
                db.signageData.where({ id: variables[index].id }).delete()
                if (!variables[index].appNewItem) {
                  db.rawData
                    .where({
                      reference: "signage",
                      id: variables[index].id,
                    })
                    .delete()
                }
                db.signageData.put(data[0] as SignageDataSchemaProps)
              }
            })
        },
      })
    }
    if (interventionData && interventionData.length) {
      interventionMutation.mutate(interventionData, {
        onSuccess(result, variables) {
          result
            .flatMap((item) => Object.values(item))
            .map(getStatusFromResult)
            .map(({ data, isSuccess }, index) => {
              if (isSuccess) {
                db.interventionData.where({ id: variables[index].id }).delete()
                if (!variables[index].appNewItem) {
                  db.rawData
                    .where({
                      reference: "intervention",
                      id: variables[index].id,
                    })
                    .delete()
                }
                db.interventionData.put(data[0] as InterventionDataSchemaProps)
              }
            })
        },
      })
    }

    if (infrastructureData && infrastructureData.length) {
      infrastructureMutation.mutate(infrastructureData, {
        onSuccess(result, variables) {
          result
            .flatMap((item) => Object.values(item))
            .map(getStatusFromResult)
            .map(({ data, isSuccess }, index) => {
              if (isSuccess) {
                db.infrastructureData
                  .where({ id: variables[index].id })
                  .delete()
                if (!variables[index].appNewItem) {
                  db.rawData
                    .where({
                      reference: "infrastructure",
                      id: variables[index].id,
                    })
                    .delete()
                }
                db.infrastructureData.put(
                  data[0] as InfrastructureDataSchemaProps
                )
              }
            })
        },
      })
    }

    if (reportData && reportData.length) {
      reportMutation.mutate(reportData, {
        onSuccess(result, variables) {
          result
            .flatMap((item) => Object.values(item))
            .map(getStatusFromResult)
            .map(({ data, isSuccess }, index) => {
              if (isSuccess) {
                db.reportData.where({ id: variables[index].id }).delete()
                if (!variables[index].appNewItem) {
                  db.rawData
                    .where({
                      reference: "report",
                      id: variables[index].id,
                    })
                    .delete()
                }
                db.reportData.put(data[0] as ReportDataSchemaProps)
              }
            })
        },
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
                        result.isError &&
                          "border-destructive bg-destructive/10 [a]:hover:bg-destructive/10!",
                        result.isSuccess &&
                          "border-green-600 [a]:hover:bg-green-600/10!"
                      )}
                    >
                      {item.pictogram && (
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
                          {item.reference} -{" "}
                          <time
                            dateTime={item.date_update}
                            className="text-xs text-muted-foreground"
                          >
                            {item.appNewItem === true
                              ? m["common.last-creation"]({
                                  date: getDurationLabel(
                                    new Date().getTime() -
                                      new Date(item.date_update).getTime(),
                                    getLocale()
                                  ),
                                })
                              : m["common.last-updated"]({
                                  date: getDurationLabel(
                                    new Date().getTime() -
                                      new Date(item.date_update).getTime(),
                                    getLocale()
                                  ),
                                })}
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
                        {result.isSuccess && (
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
        <Button className="w-full" onClick={handleSubmit}>
          {m["common.send-data"]()}
        </Button>
      </section>
    </div>
  )
}
