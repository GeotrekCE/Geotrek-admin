import { Editor } from "@tiptap/core"
import { Underline as UnderlineIcon } from "lucide-react"
import { Toggle } from "@/components/ui/toggle"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function Underline({ editor }: { editor: Editor }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Toggle
            size="sm"
            pressed={editor.isActive("underline")}
            onPressedChange={() =>
              editor.chain().focus().toggleUnderline().run()
            }
            disabled={!editor.can().chain().focus().toggleUnderline().run()}
          >
            <UnderlineIcon className="size-4" aria-hidden />
            <span className="sr-only">Souligner</span>
          </Toggle>
        }
      />
      <TooltipContent>Souligner</TooltipContent>
    </Tooltip>
  )
}
