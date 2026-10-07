export function itemToOption(item: { name: string; id: number }) {
  return {
    label: item.name,
    value: item.id,
  }
}

export function listToOptions(list: { name: string; id: number }[]) {
  return list.map(itemToOption)
}
