import { Editor } from "@tiptap/core"
import { ListOrdered } from "lucide-react"
import { Toggle } from "@/components/ui/toggle"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function OrderedList({ editor }: { editor: Editor }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Toggle
            size="sm"
            pressed={editor.isActive("orderedList")}
            onPressedChange={() =>
              editor.chain().focus().toggleOrderedList().run()
            }
          >
            <ListOrdered className="size-4" aria-hidden />
            <span className="sr-only">Liste ordonnée</span>
          </Toggle>
        }
      />
      <TooltipContent>Liste ordonnée</TooltipContent>
    </Tooltip>
  )
}
