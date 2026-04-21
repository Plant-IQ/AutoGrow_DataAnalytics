import { render, screen } from "@testing-library/react";
import useSWR from "swr";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DailyTempHumidityComparisonBarChart from "@/components/DailyTempHumidityComparisonBarChart";
import SensorChart from "@/components/SensorChart";
import SoilHumidityScatter from "@/components/SoilHumidityScatter";
import SoilMoisturePumpChart from "@/components/SoilMoisturePumpChart";
import TemperatureComparisonScatter from "@/components/TemperatureComparisonScatter";

vi.mock("swr", () => ({
  default: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  fetcher: vi.fn(),
  realFetcher: vi.fn(),
  DEFAULT_LAT: "13.7563",
  DEFAULT_LON: "100.5018",
}));

vi.mock("recharts", () => {
  const Wrap = ({ children }: { children?: React.ReactNode }) => <div>{children}</div>;
  const Stub = () => <div />;

  return {
    ResponsiveContainer: Wrap,
    LineChart: Wrap,
    ComposedChart: Wrap,
    ScatterChart: Wrap,
    BarChart: Wrap,
    CartesianGrid: Stub,
    XAxis: Stub,
    YAxis: Stub,
    Tooltip: Wrap,
    Legend: Stub,
    Line: Stub,
    Area: Stub,
    Bar: Stub,
    Scatter: Wrap,
    Cell: Stub,
    ReferenceLine: Stub,
  };
});

type SwrResult = {
  data?: unknown;
  isLoading?: boolean;
  error?: unknown;
};

const swrMock = useSWR as unknown as ReturnType<typeof vi.fn>;

function mockSWR(map: Record<string, SwrResult>) {
  swrMock.mockImplementation((key: unknown) => {
    if (key === null) return { isLoading: false, data: undefined, error: undefined };
    if (typeof key !== "string") return { isLoading: false, data: undefined, error: undefined };
    return map[key] ?? { isLoading: false, data: undefined, error: undefined };
  });
}

describe("SensorChart", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders all key states", () => {
    mockSWR({
      "/plants/active": { isLoading: true },
      "/history?until_stage=Veg": { isLoading: true },
    });
    const { rerender } = render(<SensorChart />);
    expect(screen.getByText("Loading timeline…")).toBeInTheDocument();

    mockSWR({
      "/plants/active": { data: null },
      "/history?until_stage=Veg": { data: { points: [] } },
    });
    rerender(<SensorChart />);
    expect(screen.getByText("No readings yet. Start a plant to begin collecting data.")).toBeInTheDocument();

    mockSWR({
      "/plants/active": { data: { id: 1 } },
      "/history?until_stage=Veg": { error: new Error("fail") },
    });
    rerender(<SensorChart />);
    expect(screen.getByText("Timeline unavailable")).toBeInTheDocument();

    mockSWR({
      "/plants/active": { data: { id: 1 } },
      "/history?until_stage=Veg": { data: { points: [] } },
    });
    rerender(<SensorChart />);
    expect(screen.getByText("No readings yet for this plant.")).toBeInTheDocument();
  });

  it("renders chart container when points exist", () => {
    mockSWR({
      "/plants/active": { data: { id: 1 } },
      "/history?until_stage=Veg": {
        data: {
          points: [{ ts: "2026-04-21T00:00:00Z", soil: 40, temp: 24, humidity: 60, light: 300 }],
        },
      },
    });

    render(<SensorChart />);

    expect(screen.getByText("Last readings")).toBeInTheDocument();
    expect(screen.getByText("Auto-refreshing")).toBeInTheDocument();
  });
});

describe("SoilHumidityScatter", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders loading and error states", () => {
    mockSWR({
      "/history?until_stage=Veg": { isLoading: true },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": { isLoading: true },
    });
    const { rerender } = render(<SoilHumidityScatter />);
    expect(screen.getByText("Loading soil and outdoor correlation…")).toBeInTheDocument();

    mockSWR({
      "/history?until_stage=Veg": { error: new Error("fail") },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": { data: { points: [] } },
    });
    rerender(<SoilHumidityScatter />);
    expect(screen.getByText("Correlation chart unavailable")).toBeInTheDocument();
  });

  it("renders no-data and no-match states", () => {
    mockSWR({
      "/history?until_stage=Veg": { data: { points: [] } },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": { data: { points: [] } },
    });
    const { rerender } = render(<SoilHumidityScatter />);
    expect(screen.getByText("Soil or outdoor humidity history is not available yet.")).toBeInTheDocument();

    mockSWR({
      "/history?until_stage=Veg": { data: { points: [{ ts: "2026-04-01T00:00:00Z", soil: 40 }] } },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": {
        data: { points: [{ ts: "2026-04-10T00:00:00Z", humidity: 70 }] },
      },
    });
    rerender(<SoilHumidityScatter />);
    expect(screen.getByText("No nearby soil and outdoor humidity readings could be matched yet.")).toBeInTheDocument();
  });

  it("renders scatter summary when matches exist", () => {
    mockSWR({
      "/history?until_stage=Veg": {
        data: { points: [{ ts: "2026-04-21T00:00:00Z", soil: 38 }, { ts: "2026-04-21T01:00:00Z", soil: 41 }] },
      },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": {
        data: { points: [{ ts: "2026-04-21T00:30:00Z", humidity: 72 }] },
      },
    });

    render(<SoilHumidityScatter />);

    expect(screen.getByText("Moisture correlation scatter")).toBeInTheDocument();
  });
});

describe("SoilMoisturePumpChart", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders loading, error, and empty states", () => {
    mockSWR({
      "/history?until_stage=Veg": { isLoading: true },
    });
    const { rerender } = render(<SoilMoisturePumpChart />);
    expect(screen.getByText("Loading soil moisture and pump events…")).toBeInTheDocument();

    mockSWR({
      "/history?until_stage=Veg": { error: new Error("fail") },
    });
    rerender(<SoilMoisturePumpChart />);
    expect(screen.getByText("Soil moisture chart unavailable")).toBeInTheDocument();

    mockSWR({
      "/history?until_stage=Veg": { data: { points: [] } },
    });
    rerender(<SoilMoisturePumpChart />);
    expect(screen.getByText("Soil moisture history is not available yet.")).toBeInTheDocument();
  });

  it("renders moisture chart summary", () => {
    mockSWR({
      "/history?until_stage=Veg": {
        data: {
          points: [
            { ts: "2026-04-21T00:00:00Z", soil: 39, pump_on: false },
            { ts: "2026-04-21T01:00:00Z", soil: 52, pump_on: true },
          ],
        },
      },
    });

    render(<SoilMoisturePumpChart />);

    expect(screen.getByText("Soil moisture with pump events")).toBeInTheDocument();
    expect(screen.getByText("Pump ON")).toBeInTheDocument();
  });
});

describe("TemperatureComparisonScatter", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders loading and error states", () => {
    mockSWR({
      "/history?until_stage=Veg": { isLoading: true },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": { isLoading: true },
    });
    const { rerender } = render(<TemperatureComparisonScatter />);
    expect(screen.getByText("Loading temperature correlation…")).toBeInTheDocument();

    mockSWR({
      "/history?until_stage=Veg": { error: new Error("fail") },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": { data: { points: [] } },
    });
    rerender(<TemperatureComparisonScatter />);
    expect(screen.getByText("Temperature comparison unavailable")).toBeInTheDocument();
  });

  it("renders no-data and no-match states", () => {
    mockSWR({
      "/history?until_stage=Veg": { data: { points: [] } },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": { data: { points: [] } },
    });
    const { rerender } = render(<TemperatureComparisonScatter />);
    expect(screen.getByText(/Glasshouse or outdoor temperature history is not available yet/)).toBeInTheDocument();

    mockSWR({
      "/history?until_stage=Veg": { data: { points: [{ ts: "2026-04-01T00:00:00Z", temp: 25 }] } },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": {
        data: { points: [{ ts: "2026-04-10T00:00:00Z", temperature_2m: 30 }] },
      },
    });
    rerender(<TemperatureComparisonScatter />);
    expect(screen.getByText(/No nearby glasshouse and outdoor temperature readings could be matched yet/)).toBeInTheDocument();
  });

  it("renders comparison summary when points match", () => {
    mockSWR({
      "/history?until_stage=Veg": { data: { points: [{ ts: "2026-04-21T00:00:00Z", temp: 28 }] } },
      "/outdoor/history?lat=13.7563&lon=100.5018&past_days=7": {
        data: { points: [{ ts: "2026-04-21T00:30:00Z", temperature_2m: 30 }] },
      },
    });

    render(<TemperatureComparisonScatter />);
    expect(screen.getByText("Temperature comparison scatter")).toBeInTheDocument();
  });
});

describe("DailyTempHumidityComparisonBarChart", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders loading and error states", () => {
    mockSWR({
      "/history?until_stage=Veg": { isLoading: true },
      "/outdoor/daily-avg?lat=13.7563&lon=100.5018&past_days=7": { isLoading: true },
    });
    const { rerender } = render(<DailyTempHumidityComparisonBarChart />);
    expect(screen.getByText("Loading daily comparisons…")).toBeInTheDocument();

    mockSWR({
      "/history?until_stage=Veg": { error: new Error("fail") },
      "/outdoor/daily-avg?lat=13.7563&lon=100.5018&past_days=7": { data: { points: [] } },
    });
    rerender(<DailyTempHumidityComparisonBarChart />);
    expect(screen.getByText("Daily comparison unavailable")).toBeInTheDocument();
  });

  it("renders empty and success states", () => {
    mockSWR({
      "/history?until_stage=Veg": { data: { points: [] } },
      "/outdoor/daily-avg?lat=13.7563&lon=100.5018&past_days=7": { data: { points: [] } },
    });
    const { rerender } = render(<DailyTempHumidityComparisonBarChart />);
    expect(screen.getByText("Daily glasshouse averages are not available yet.")).toBeInTheDocument();

    mockSWR({
      "/history?until_stage=Veg": {
        data: {
          points: [
            { ts: "2026-04-20T00:00:00Z", temp: 30, humidity: 70 },
            { ts: "2026-04-20T12:00:00Z", temp: 32, humidity: 66 },
            { ts: "2026-04-21T12:00:00Z", temp: 31, humidity: 68 },
          ],
        },
      },
      "/outdoor/daily-avg?lat=13.7563&lon=100.5018&past_days=7": {
        data: {
          points: [
            { date: "2026-04-20", avg_temp: 29 },
            { date: "2026-04-21", avg_temp: 30 },
          ],
        },
      },
    });
    rerender(<DailyTempHumidityComparisonBarChart />);

    expect(screen.getByText("Glasshouse vs outdoor daily averages")).toBeInTheDocument();
  });
});
