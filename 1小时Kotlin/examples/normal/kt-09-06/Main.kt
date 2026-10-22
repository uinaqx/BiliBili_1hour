package lessons.kt_09_06
fun main() {
    val scores = listOf(58, 60, 90)
    val result = scores.map { it + 2 }.filter { it >= 60 }
    println(result)
}
