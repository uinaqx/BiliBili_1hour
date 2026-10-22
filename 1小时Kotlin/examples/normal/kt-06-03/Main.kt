package lessons.kt_06_03
fun main() {
    val scores = listOf(80, 90, 70)
    var total = 0
    for (score in scores) {
        total += score
    }
    val average = total.toDouble() / scores.size
    println(average)
}
