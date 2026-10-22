package lessons.kt_07_04
fun main() {
    val text = "八十五"
    val score = text.toIntOrNull()
    if (score == null) {
        println("请输入阿拉伯数字")
    } else {
        println(score + 5)
    }
}
