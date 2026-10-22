package lessons.kt_09_03
fun main() {
    val scores = listOf(55, 80, 92)
    val result = scores
        .filter { it >= 60 }
        .map { it + 5 }
    println(result)
}
