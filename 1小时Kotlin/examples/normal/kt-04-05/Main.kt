package lessons.kt_04_05
fun main() {
    var total = 0
    for (score in listOf(80, 90, 70)) {
        total += score
    }
    println(total)
}
