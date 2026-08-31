import { Editor } from "@tiptap/core"
import { List } from "lucide-react"
import { Toggle } from "@/components/ui/toggle"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function BulletList({ editor }: { editor: Editor }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Toggle
            size="sm"
            pressed={editor.isActive("bulletList")}
            onPressedChange={() =>
              editor.chain().focus().toggleBulletList().run()
            }
          >
            <List className="size-4" aria-hidden />
            <span className="sr-only">Liste</span>
          </Toggle>
        }
      />
      <TooltipContent>Liste</TooltipContent>
    </Tooltip>
  )
}
