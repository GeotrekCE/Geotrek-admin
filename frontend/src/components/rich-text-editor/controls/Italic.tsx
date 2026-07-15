import { Editor } from "@tiptap/core"
import { Italic as ItalicIcon } from "lucide-react"
import { Toggle } from "@/components/ui/toggle"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function Italic({ editor }: { editor: Editor }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Toggle
            size="sm"
            pressed={editor.isActive("italic")}
            onPressedChange={() => editor.chain().focus().toggleItalic().run()}
            disabled={!editor.can().chain().focus().toggleItalic().run()}
          >
            <ItalicIcon className="size-4" aria-hidden />
            <span className="sr-only">Italique</span>
          </Toggle>
        }
      />
      <TooltipContent>Italique</TooltipContent>
    </Tooltip>
  )
}
