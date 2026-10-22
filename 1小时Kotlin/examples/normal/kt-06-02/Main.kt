package lessons.kt_06_02
fun main() {
    val scores = mutableListOf(80, 90)
    scores.add(70)
    scores[0] = 85
    scores.removeAt(1)
    println(scores)
}
