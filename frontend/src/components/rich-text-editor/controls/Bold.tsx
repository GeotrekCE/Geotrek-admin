import { Editor } from "@tiptap/core"
import { Bold as BoldIcon } from "lucide-react"
import { Toggle } from "@/components/ui/toggle"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function Bold({ editor }: { editor: Editor }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Toggle
            size="sm"
            pressed={editor.isActive("bold")}
            onPressedChange={() => editor.chain().focus().toggleBold().run()}
            disabled={!editor.can().chain().focus().toggleBold().run()}
          >
            <BoldIcon className="size-4" aria-hidden />
            <span className="sr-only">Gras</span>
          </Toggle>
        }
      />
      <TooltipContent>Gras</TooltipContent>
    </Tooltip>
  )
}
