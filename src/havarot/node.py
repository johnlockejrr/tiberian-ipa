"""Bidirectional linked-list node (ported from havarotjs)."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class Node(Generic[T]):
    """Node in a bidirectional chain with optional child nodes."""

    def __init__(self) -> None:
        self.value: Optional[T] = None
        self.next: Optional["Node[T]"] = None
        self.prev: Optional["Node[T]"] = None
        self.child: Optional["Node[T]"] = None

    @property
    def children(self) -> None:
        raise AttributeError("children is write-only")

    @children.setter
    def children(self, arr: List["Node[T]"]) -> None:
        if not arr:
            self.child = None
            return
        head = arr[0]
        remainder = arr[1:]
        self.child = head
        head.siblings = remainder

    @property
    def siblings(self) -> List["Node[T]"]:
        curr = self.next
        res: List["Node[T]"] = []
        while curr:
            res.append(curr)
            curr = curr.next
        return res

    @siblings.setter
    def siblings(self, arr: List["Node[T]"]) -> None:
        length = len(arr)
        for index in range(length):
            curr = arr[index]
            nxt = arr[index + 1] if index + 1 < length else None
            prv = arr[index - 1] if index - 1 >= 0 else self
            curr.prev = prv
            prv.next = curr
            curr.next = nxt
