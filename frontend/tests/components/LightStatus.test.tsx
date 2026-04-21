/* eslint-disable @next/next/no-img-element */
import { render, screen } from "@testing-library/react";
import type { ComponentProps } from "react";
import useSWR from "swr";
import { describe, expect, it, vi } from "vitest";

import LightStatus from "@/components/LightStatus";

vi.mock("swr", () => ({
  default: vi.fn(),
}));

vi.mock("next/image", () => ({
  default: ({ alt = "", ...props }: ComponentProps<"img">) => <img alt={alt} {...props} />,
}));

type SwrResult = {
  data?: unknown;
  isLoading?: boolean;
  error?: unknown;
};

function renderWithSWRMap(map: Record<string, SwrResult>) {
  const swrMock = useSWR as unknown as ReturnType<typeof vi.fn>;
  swrMock.mockImplementation((key: unknown) => {
    if (key === null) return { isLoading: false, data: undefined, error: undefined };
    if (typeof key !== "string") return { isLoading: false, data: undefined, error: undefined };
    return map[key] ?? { isLoading: false, data: undefined, error: undefined };
  });
  return render(<LightStatus />);
}

describe("LightStatus", () => {
  it("renders loading state with full-height class", () => {
    const { container } = renderWithSWRMap({
      "/plants/active": { isLoading: true },
    });

    expect(screen.getByText("Loading light status…")).toBeInTheDocument();
    expect(container.querySelector(".card")?.className).toContain("h-full");
  });

  it("renders empty state with full-height class when no active plant", () => {
    const { container } = renderWithSWRMap({
      "/plants/active": { data: null, isLoading: false },
      "/light": { data: { spectrum: "", hours_today: 0 }, isLoading: false },
      "/history": { data: { points: [] }, isLoading: false },
    });

    expect(screen.getByText("Light is off until a new plant starts.")).toBeInTheDocument();
    expect(container.querySelector(".card")?.className).toContain("h-full");
  });

  it("renders unavailable state with full-height class on error", () => {
    const { container } = renderWithSWRMap({
      "/plants/active": { data: null, isLoading: false, error: new Error("boom") },
    });

    expect(screen.getByText("Light status unavailable")).toBeInTheDocument();
    expect(container.querySelector(".card")?.className).toContain("h-full");
  });

  it("renders live light status and latest lux", () => {
    renderWithSWRMap({
      "/plants/active": {
        data: {
          id: 10,
          label: "Lettuce",
          plant_type_id: 1,
          current_stage_index: 1,
          stage_started_at: "2026-01-01T00:00:00Z",
          pending_confirm: false,
        },
      },
      "/plants/10/light": {
        data: { plant_id: 10, stage: 1, color: "#FFFFFF", pending_confirm: false },
      },
      "/light": { data: { spectrum: "white", hours_today: 6 } },
      "/history": {
        data: { points: [{ ts: "2026-01-01T00:00:00Z", light: 123.45 }] },
      },
    });

    expect(screen.getByText("Light Status")).toBeInTheDocument();
    expect(screen.getByText("White")).toBeInTheDocument();
    expect(screen.getByText("Auto-sync")).toBeInTheDocument();
    expect(screen.getByText("123.5 lux")).toBeInTheDocument();
  });
});
