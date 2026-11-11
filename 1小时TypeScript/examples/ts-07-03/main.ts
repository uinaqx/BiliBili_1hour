class Report {
  title(): string { return "开销记录"; }
}
class MonthlyReport extends Report {
  override title(): string {
    return super.title() + "：本月";
  }
}
console.log(new MonthlyReport().title());

export {};
