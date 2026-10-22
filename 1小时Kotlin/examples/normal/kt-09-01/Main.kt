package lessons.kt_09_01
fun main() {
    val scores = listOf(80, 90, 70)
    val improved = scores.map { score -> score + 5 }
    println(improved)
    println(scores)
}
