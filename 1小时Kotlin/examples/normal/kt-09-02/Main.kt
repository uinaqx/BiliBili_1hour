package lessons.kt_09_02
fun main() {
    val scores = listOf(55, 80, 92, 40)
    val passed = scores.filter { score -> score >= 60 }
    println(passed)
    println(passed.size)
}
