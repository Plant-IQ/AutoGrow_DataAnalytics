import HarvestETA from "@/components/HarvestETA";
import HealthGauge from "@/components/HealthGauge";
import ObsForm from "@/components/ObsForm";
import PumpStatus from "@/components/PumpStatus";
import SensorChart from "@/components/SensorChart";
import StageCard from "@/components/StageCard";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white text-slate-900">
      <header className="border-b border-slate-200 bg-white/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-emerald-600">AutoGrow</p>
            <h1 className="text-2xl font-semibold">Grow room overview</h1>
          </div>
          <div className="rounded-full bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-700">
            Live mock data
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-8">
        <div className="grid gap-4 md:grid-cols-3">
          <StageCard />
          <HarvestETA />
          <PumpStatus />
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <HealthGauge />
          <div className="lg:col-span-2">
            <SensorChart />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <ObsForm />
          <div className="card">
            <p className="label">Notes</p>
            <p className="text-sm text-slate-600">
              Use this panel during class to demo how you collected data. Screen-share or bring your laptop and
              walk through sensor setup, sampling cadence, and any issues you hit so we can troubleshoot together.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
