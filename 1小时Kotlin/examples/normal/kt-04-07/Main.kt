package lessons.kt_04_07
fun main() {
    var total = 0
    for (n in 1..4) {
        if (n == 3) continue
        total += n
    }
    println(total)
}
