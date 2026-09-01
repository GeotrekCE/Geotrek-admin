import * as React from "react"
import { PencilIcon } from "lucide-react"
import { useSelector } from "@tanstack/react-form"
import { Input } from "@/components/ui/input"
import { FieldDescription, FieldLabel } from "@/components/ui/field"
import {
  useFieldContext,
  FormFieldSet,
  FormField,
  FormFieldError,
  createFormField,
} from "@/components/ui/form-context"
import { Spinner } from "@/components/ui/spinner"
import Required from "./required"
import { cn } from "@/lib/utils"

interface TextFieldProps extends Omit<
  React.ComponentProps<"input">,
  "value" | "onChange" | "onBlur"
> {
  label: string
  description?: string
  required?: boolean
}

export function FileUploadField({
  label,
  description,
  required,
  className,
  ...inputProps
}: TextFieldProps) {
  const id = React.useId()
  const field = useFieldContext()
  const isTouched = useSelector(field.store, (s) => s.meta.isTouched)
  const isValid = useSelector(field.store, (s) => s.meta.isValid)
  const isValidating = useSelector(field.store, (s) => s.meta.isValidating)
  const value = useSelector(field.store, (s) => s.value)

  const isImage = inputProps.accept?.includes("image") || false

  const handleChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0]
      field.handleChange(file)
    }
  }

  if (isImage) {
    return (
      <FormFieldSet>
        <FormField>
          <label htmlFor={id} className="group relative cursor-pointer">
            <span className="sr-only">{label}</span>
            <span className="">
              {value && value instanceof File ? (
                <img
                  src={URL.createObjectURL(value)}
                  alt=""
                  className="size-30 rounded-lg bg-primary/15 object-contain"
                />
              ) : (
                <span className="flex size-30 items-center justify-center rounded-lg bg-primary/15">
                  <PencilIcon className="size-6 text-primary/90" />
                </span>
              )}
              <Input
                id={id}
                type="file"
                onBlur={field.handleBlur}
                onChange={handleChange}
                aria-invalid={isTouched && !isValid}
                className={cn("sr-only", className)}
                data-testid={`field-${field.name}`}
                name={field.name}
                {...inputProps}
              />
            </span>
            {required && <Required />}
          </label>
          {description && <FieldDescription>{description}</FieldDescription>}
        </FormField>
        <FormFieldError />
      </FormFieldSet>
    )
  }

  return (
    <FormFieldSet>
      <FormField>
        <FieldLabel htmlFor={id} className="font-normal text-accent-foreground">
          {label}
          {required && <Required />}
        </FieldLabel>
        <div className="relative">
          <Input
            id={id}
            type="file"
            onBlur={field.handleBlur}
            onChange={handleChange}
            aria-invalid={isTouched && !isValid}
            className={className}
            data-testid={`field-${field.name}`}
            name={field.name}
            {...inputProps}
          />
          {isValidating && (
            <div className="absolute top-1/2 right-3 -translate-y-1/2">
              <Spinner className="h-4 w-4" />
            </div>
          )}
        </div>
        {description && <FieldDescription>{description}</FieldDescription>}
      </FormField>
      <FormFieldError />
    </FormFieldSet>
  )
}
export const FormFileUploadField = createFormField(FileUploadField)
