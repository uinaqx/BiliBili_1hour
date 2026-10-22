package lessons.kt_09_04
fun Int.isPassing(): Boolean {
    return this >= 60
}
fun main() {
    println(85.isPassing())
    println(40.isPassing())
}
