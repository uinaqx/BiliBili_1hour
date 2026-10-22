package lessons.kt_05_06
fun increase(value: Int): Int {
    return value + 1
}
fun main() {
    val score = 80
    val nextScore = increase(score)
    println(score)
    println(nextScore)
}
