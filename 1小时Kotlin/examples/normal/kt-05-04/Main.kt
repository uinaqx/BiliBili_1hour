package lessons.kt_05_04
fun finalScore(score: Int, bonus: Int = 5): Int {
    return score + bonus
}
fun main() {
    println(finalScore(80))
    println(finalScore(score = 80, bonus = 10))
}
