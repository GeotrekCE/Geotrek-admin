import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function itemToOption(item: { name: string; id: number }) {
  return {
    label: item.name,
    value: item.id,
  }
}

export function listToOptions(list: { name: string; id: number }[]) {
  return list.map(itemToOption)
}
