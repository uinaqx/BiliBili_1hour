package lessons.kt_06_07
fun main() {
    val scores = mutableListOf(80, 90, 70)
    scores.removeAt(0)
    println(scores[0])
    println(scores.size)
}
