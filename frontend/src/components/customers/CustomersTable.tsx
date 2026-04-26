import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  ArrowDownIcon,
  ArrowUpDownIcon,
  ArrowUpIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from "lucide-react";
import { useMemo } from "react";

import type { CustomerListItem, CustomerSort } from "@/api/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatPercent } from "@/lib/format";
import { humanizeIndustry } from "@/lib/labels";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 20;

interface CustomersTableProps {
  data: CustomerListItem[] | undefined;
  total: number;
  skip: number;
  isLoading: boolean;
  sort: CustomerSort;
  onSortChange: (next: CustomerSort) => void;
  onPageChange: (skip: number) => void;
  onRowClick: (customerId: number) => void;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function CustomersTable({
  data,
  total,
  skip,
  isLoading,
  sort,
  onSortChange,
  onPageChange,
  onRowClick,
}: CustomersTableProps) {
  const columns = useMemo<ColumnDef<CustomerListItem>[]>(
    () => [
      {
        id: "customer_name",
        accessorKey: "customer_name",
        header: () => "Cliente",
      },
      {
        id: "seller_name",
        accessorKey: "seller_name",
        header: () => "Vendedor",
      },
      {
        id: "meeting_date",
        accessorKey: "meeting_date",
        header: () => "Fecha",
        cell: ({ row }) => formatDate(row.original.meeting_date),
      },
      {
        id: "industry",
        accessorKey: "industry",
        header: () => "Industria",
        cell: ({ row }) =>
          row.original.industry ? (
            <span className="text-sm">{humanizeIndustry(row.original.industry)}</span>
          ) : (
            <span className="text-xs text-muted-foreground">sin categorizar</span>
          ),
      },
      {
        id: "status",
        header: () => "Estado",
        cell: ({ row }) => (
          <div className="flex items-center gap-2">
            <Badge variant={row.original.closed ? "default" : "secondary"}>
              {row.original.closed ? "Cerrada" : "Abierta"}
            </Badge>
            {row.original.close_probability !== null ? (
              <span className="text-xs text-muted-foreground tabular-nums">
                {formatPercent(row.original.close_probability, 0)}
              </span>
            ) : null}
          </div>
        ),
      },
    ],
    [],
  );

  const table = useReactTable({
    data: data ?? [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const sortableColumns: Record<string, { asc: CustomerSort; desc: CustomerSort }> = {
    customer_name: { asc: "customer_name_asc", desc: "customer_name_desc" },
    meeting_date: { asc: "meeting_date_asc", desc: "meeting_date_desc" },
  };

  function handleHeaderClick(columnId: string) {
    const sortable = sortableColumns[columnId];
    if (!sortable) return;
    if (sort === sortable.desc) onSortChange(sortable.asc);
    else onSortChange(sortable.desc);
  }

  function sortIcon(columnId: string) {
    const sortable = sortableColumns[columnId];
    if (!sortable) return null;
    if (sort === sortable.asc) return <ArrowUpIcon className="h-3 w-3" />;
    if (sort === sortable.desc) return <ArrowDownIcon className="h-3 w-3" />;
    return <ArrowUpDownIcon className="h-3 w-3 opacity-50" />;
  }

  const page = Math.floor(skip / PAGE_SIZE) + 1;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="space-y-3">
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((group) => (
              <TableRow key={group.id}>
                {group.headers.map((header) => {
                  const isSortable = header.column.id in sortableColumns;
                  return (
                    <TableHead
                      key={header.id}
                      className={cn(isSortable && "cursor-pointer select-none")}
                      onClick={() => isSortable && handleHeaderClick(header.column.id)}
                    >
                      <div className="flex items-center gap-2">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {sortIcon(header.column.id)}
                      </div>
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {columns.map((_col, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-24" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : table.getRowModel().rows.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-sm text-muted-foreground"
                >
                  Sin clientes para los filtros activos.
                </TableCell>
              </TableRow>
            ) : (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  className="cursor-pointer"
                  onClick={() => onRowClick(row.original.customer_id)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          {total === 0 ? "0" : `${skip + 1}–${Math.min(skip + PAGE_SIZE, total)}`} de{" "}
          {total}
        </span>
        <div className="flex items-center gap-2">
          <span>
            Página {page} de {totalPages}
          </span>
          <Button
            variant="outline"
            size="icon"
            disabled={skip === 0}
            onClick={() => onPageChange(Math.max(0, skip - PAGE_SIZE))}
            aria-label="Página anterior"
          >
            <ChevronLeftIcon className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            disabled={skip + PAGE_SIZE >= total}
            onClick={() => onPageChange(skip + PAGE_SIZE)}
            aria-label="Página siguiente"
          >
            <ChevronRightIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
