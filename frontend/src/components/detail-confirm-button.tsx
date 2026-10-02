import * as React from "react"
import { m } from "@/paraglide/messages"
import { Button } from "@/components/ui/button"
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "@/components/ui/popover"

export default function DetailConfirmButton({
  onClick,
  reason,
  ...props
}: React.ComponentProps<typeof Button> & { reason: string }) {
  const [open, setOpen] = React.useState(false)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        render={<Button {...props}>{reason}</Button>}
      ></PopoverTrigger>
      <PopoverContent align="center" side="top">
        <PopoverHeader>
          <PopoverTitle>
            <strong>
              {m["content.confirm-dialog-title"]({
                reason: reason.toLocaleLowerCase(),
              })}
            </strong>
          </PopoverTitle>
          <PopoverDescription>
            {m["content.confirm-dialog-description"]()}
          </PopoverDescription>
        </PopoverHeader>
        <Button onClick={() => setOpen(false)} variant="outline">
          {m["common.cancel"]()}
        </Button>
        <Button
          onClick={(event) => {
            event.preventDefault()
            onClick?.(event)
            scrollTo({ top: 0, behavior: "smooth" })
          }}
          type="reset"
        >
          {m["common.confirm"]()}
        </Button>
      </PopoverContent>
    </Popover>
  )
}
