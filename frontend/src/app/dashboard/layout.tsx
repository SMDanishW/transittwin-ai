import Header from "@/components/ui/Header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-full">
      <Header />
      <div className="flex flex-1 overflow-hidden">{children}</div>
    </div>
  );
}
