import * as React from "react"
import { useStore } from "@tanstack/react-form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Combobox,
  ComboboxChip,
  ComboboxChips,
  ComboboxChipsInput,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxItem,
  ComboboxList,
  ComboboxValue,
} from "@/components/ui/combobox"
import { FieldDescription, FieldLabel } from "@/components/ui/field"
import {
  useFieldContext,
  FormFieldSet,
  FormField,
  FormFieldError,
  createFormField,
} from "@/components/ui/form-context"
import Required from "./required"
import { cn, itemToOption, listToOptions } from "@/lib/utils"
import { ChevronDown } from "lucide-react"

type List = { name: string; id: number }

interface SelectFieldProps {
  label: string
  description?: string
  required?: boolean
  list: List[]
  placeholder?: string
  multiple?: boolean
  className?: string
}

export function SelectField({
  label,
  description,
  required,
  list,
  placeholder = "Sélectionnez",
  multiple = false,
  className,
}: SelectFieldProps) {
  const id = React.useId()
  const field = useFieldContext()
  const isTouched = useStore(field.store, (s) => s.meta.isTouched)
  const isValid = useStore(field.store, (s) => s.meta.isValid)
  const rawValue = useStore(field.store, (s) => s.value)

  const comboboxValue = multiple ? listToOptions(rawValue as List[]) : undefined
  const selectValue =
    !multiple && rawValue ? itemToOption(rawValue as List) : undefined

  return (
    <FormFieldSet>
      <FormField>
        <FieldLabel htmlFor={id} className="font-normal text-accent-foreground">
          {label}
          {required && <Required />}
        </FieldLabel>
        {multiple && (
          <Combobox
            id={id}
            multiple
            autoHighlight
            items={listToOptions(list)}
            value={comboboxValue}
            onValueChange={(selectedItem) => {
              if (selectedItem) {
                field.handleChange(
                  selectedItem.map((item) => ({
                    name: item.label,
                    id: item.value,
                  }))
                )
              } else {
                field.handleChange([])
              }
            }}
            aria-invalid={isTouched && !isValid}
            isItemEqualToValue={(itemValue, selectedValue) =>
              itemValue?.value === selectedValue?.value
            }
          >
            <ComboboxChips className={cn("relative w-full", className)}>
              <ComboboxValue>
                {(values) => (
                  <React.Fragment>
                    {values.map((value: { value: number; label: string }) => (
                      <ComboboxChip key={value.value}>
                        {value.label}
                      </ComboboxChip>
                    ))}
                    <ComboboxChipsInput />
                    <ChevronDown
                      className="pointer-events-none absolute inset-e-2 bottom-2 size-4 shrink-0 cursor-pointer"
                      aria-hidden
                    />
                  </React.Fragment>
                )}
              </ComboboxValue>
            </ComboboxChips>
            <ComboboxContent>
              <ComboboxEmpty>Aucun état trouvé</ComboboxEmpty>
              <ComboboxList>
                {(item) => (
                  <ComboboxItem key={item.value} value={item}>
                    {item.label}
                  </ComboboxItem>
                )}
              </ComboboxList>
            </ComboboxContent>
          </Combobox>
        )}
        {!multiple && (
          <Select
            items={listToOptions(list)}
            value={selectValue}
            onValueChange={(value) =>
              field.handleChange(
                list.find((item) => item.id === Number(value)) ?? list[0]
              )
            }
            onOpenChange={(open) => {
              if (!open) field.handleBlur()
            }}
          >
            <SelectTrigger
              id={id}
              aria-invalid={isTouched && !isValid}
              className={className}
            >
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {list.map((opt) => (
                <SelectItem key={opt.id} value={opt.id}>
                  {opt.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
        {description && <FieldDescription>{description}</FieldDescription>}
      </FormField>
      <FormFieldError />
    </FormFieldSet>
  )
}

export const FormSelectField = createFormField(SelectField)
