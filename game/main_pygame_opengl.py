import os
import pygame
import live2d.v3 as l2d_v3
import resources
from OpenGL.GL import *

import faulthandler
faulthandler.enable()


def draw_pygame_background(screen_surface, background_image):
    """Draw background using pygame and convert to OpenGL texture"""
    # Convert pygame surface to OpenGL texture
    background_data = pygame.image.tostring(background_image, "RGBA", True)
    width, height = background_image.get_size()

    # Create texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, background_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    # Draw textured quad
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(-1, -1)
    glTexCoord2f(1, 0)
    glVertex2f(1, -1)
    glTexCoord2f(1, 1)
    glVertex2f(1, 1)
    glTexCoord2f(0, 1)
    glVertex2f(-1, 1)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDeleteTextures(1, [texture])


class Whiteboard:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill((255, 255, 255, 200))  # 半透明白色
        self.drawing = False
        self.last_pos = None
        self.mode = "pen"  # pen or eraser
        self.pen_size = 3
        self.eraser_size = 15
        self.history = []  # 用于撤销功能的历史记录

    def start_drawing(self, pos):
        # 开始绘图
        if self.rect.collidepoint(pos):
            self.drawing = True
            self.last_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
            self.save_state()

    def stop_drawing(self):
        # 停止绘图
        self.drawing = False
        self.last_pos = None

    def draw_line(self, start, end):
        # 在白板上绘制线条
        size = self.pen_size if self.mode == "pen" else self.eraser_size
        color = (0, 0, 0) if self.mode == "pen" else (255, 255, 255, 0)
        pygame.draw.line(self.surface, color, start, end, size)

    def update_drawing(self, pos):
        # 更新绘图过程
        if self.drawing and self.last_pos:
            current_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
            if self.rect.collidepoint(pos):
                self.draw_line(self.last_pos, current_pos)
                self.last_pos = current_pos

    def save_state(self):
        # 保存当前状态用于撤销功能
        self.history.append(self.surface.copy())
        # 限制历史记录数量以节省内存
        if len(self.history) > 10:
            self.history.pop(0)

    def undo(self):
        # 撤销上一步操作
        if self.history:
            self.surface = self.history.pop()

    def clear(self):
        # 清空白板
        self.save_state()  # 保存当前状态以便可以撤销清空操作
        self.surface.fill((255, 255, 255, 200))

    def get_surface(self):
        # 返回白板表面
        return self.surface

    def get_rect(self):
        # 返回白板矩形
        return self.rect


def draw_texture_at_position(texture_data, width, height, x, y, display):
    """在指定位置绘制纹理，自动处理坐标系统转换"""
    # 将表面转换为OpenGL纹理
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

    # 计算在屏幕上的位置（标准化设备坐标），自动处理坐标系统差异
    x_ratio = width / display[0]
    y_ratio = height / display[1]
    x_offset = (x / display[0]) * 2 - 1
    # OpenGL的Y坐标需要翻转（pygame的y坐标是从上到下增加的，OpenGL是从下到上增加的）
    y_offset = 1 - (y / display[1]) * 2

    # 绘制纹理
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)

    glBegin(GL_QUADS)
    # 左下角
    glTexCoord2f(0, 0)  # 纹理坐标左下角
    glVertex2f(x_offset, y_offset - y_ratio * 2)  # 屏幕坐标左下角
    # 右下角
    glTexCoord2f(1, 0)  # 纹理坐标右下角
    glVertex2f(x_offset + x_ratio * 2, y_offset - y_ratio * 2)  # 屏幕坐标右下角
    # 右上角
    glTexCoord2f(1, 1)  # 纹理坐标右上角
    glVertex2f(x_offset + x_ratio * 2, y_offset)  # 屏幕坐标右上角
    # 左上角
    glTexCoord2f(0, 1)  # 纹理坐标左上角
    glVertex2f(x_offset, y_offset)  # 屏幕坐标左上角
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDeleteTextures(1, [texture])


def draw_whiteboard(whiteboard, display):
    """只绘制白板区域，不绘制整个屏幕"""
    # 将白板表面转换为OpenGL纹理
    whiteboard_surface = whiteboard.get_surface()
    whiteboard_rect = whiteboard.get_rect()
    whiteboard_data = pygame.image.tostring(whiteboard_surface, "RGBA", True)

    # 使用统一的绘制函数处理坐标系统转换
    draw_texture_at_position(whiteboard_data, whiteboard_rect.width, whiteboard_rect.height,
                             whiteboard_rect.x, whiteboard_rect.y, display)


def draw_tool_buttons(tool_buttons, whiteboard, font, display):
    """绘制工具按钮"""
    # 创建一个只包含按钮区域的临时表面
    # 计算包含所有按钮的最小矩形
    all_buttons_rect = pygame.Rect(tool_buttons["pen"])
    for button in tool_buttons.values():
        all_buttons_rect.union_ip(button)
    
    # 创建只包含按钮区域的表面，填充透明背景
    button_surface = pygame.Surface(
        (all_buttons_rect.width, all_buttons_rect.height), pygame.SRCALPHA)
    # 填充完全透明的背景以避免黑色背景
    button_surface.fill((0, 0, 0, 0))

    # 绘制工具按钮
    for tool, button in tool_buttons.items():
        # 调整按钮位置到局部坐标
        local_button = pygame.Rect(button.x - all_buttons_rect.x, button.y - all_buttons_rect.y,
                                   button.width, button.height)
        color = (200, 200, 255) if whiteboard.mode == tool else (200, 200, 200)
        pygame.draw.rect(button_surface, color, local_button)
        pygame.draw.rect(button_surface, (100, 100, 100), local_button, 2)

        # 绘制按钮文字
        text = font.render(tool.capitalize(), True, (0, 0, 0))
        text_rect = text.get_rect(center=local_button.center)
        button_surface.blit(text, text_rect)

    # 将按钮表面转换为OpenGL纹理
    button_data = pygame.image.tostring(button_surface, "RGBA", True)

    # 使用统一的绘制函数处理坐标系统转换
    draw_texture_at_position(button_data, all_buttons_rect.width, all_buttons_rect.height,
                             all_buttons_rect.x, all_buttons_rect.y, display)


def draw_mode_indicator(whiteboard, font, display):
    """绘制当前模式指示器"""
    # 创建一个小表面来显示模式文本
    mode_text = font.render(
        f"Mode: {whiteboard.mode.capitalize()}", True, (0, 0, 0))
    mode_surface = pygame.Surface(
        (mode_text.get_width() + 20, mode_text.get_height() + 10), pygame.SRCALPHA)
    mode_surface.fill((255, 255, 255, 180))  # 半透明白色背景
    mode_surface.blit(mode_text, (10, 5))

    # 将表面转换为OpenGL纹理
    mode_data = pygame.image.tostring(mode_surface, "RGBA", True)

    # 计算位置（在白板上方）
    x_pos = display[0]//2 - 300  # 白板左侧
    y_pos = display[1]//2 - 220  # 白板上方20像素

    # 使用统一的绘制函数处理坐标系统转换
    draw_texture_at_position(mode_data, mode_surface.get_width(), mode_surface.get_height(),
                             x_pos, y_pos, display)


def main():
    pygame.init()
    l2d_v3.init()

    display = (1280, 800)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("pygame window")

    l2d_v3.glewInit()

    model_v3 = l2d_v3.LAppModel()
    model_v3_2 = l2d_v3.LAppModel()

    # Load background image using pygame
    background_image = pygame.image.load(
        os.path.join(resources.RESOURCES_DIRECTORY, "RING.png")
    )
    # Scale background to fit the display
    background_image = pygame.transform.scale(background_image, display)

    model_v3.LoadModelJson(
        os.path.join(resources.RESOURCES_DIRECTORY, "v3/llny/llny.model3.json")
    )
    model_v3_2.LoadModelJson(
        os.path.join(resources.RESOURCES_DIRECTORY, "v3/Haru/Haru.model3.json")
    )

    model_v3.Resize(*display)
    model_v3_2.Resize(*display)

    model_v3.SetOffset(-1.2, 0.0)
    model_v3_2.SetOffset(1.2, 0.0)

    # 创建白板实例（位于屏幕中央）
    whiteboard = Whiteboard(display[0]//2 - 300, display[1]//2 - 200, 600, 400)

    # 工具按钮位置
    tool_buttons = {
        "pen": pygame.Rect(display[0]//2 - 290, display[1]//2 + 210, 100, 40),
        "eraser": pygame.Rect(display[0]//2 - 180, display[1]//2 + 210, 100, 40),
        "undo": pygame.Rect(display[0]//2 - 70, display[1]//2 + 210, 100, 40),
        "clear": pygame.Rect(display[0]//2 + 40, display[1]//2 + 210, 100, 40)
    }

    # 创建字体，使用系统可用的英文字体避免乱码
    pygame.font.init()
    try:
        # 尝试使用Arial字体
        font = pygame.font.Font(
            "/System/Library/Fonts/Supplemental/Arial.ttf", 24)
    except FileNotFoundError:
        try:
            # 如果Arial不可用，尝试使用Arial Unicode
            font = pygame.font.Font(
                "/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 24)
        except FileNotFoundError:
            # 如果都不可用，使用默认字体
            font = pygame.font.Font(None, 24)

    # 添加时钟用于控制动画
    clock = pygame.time.Clock()

    # 记录时间用于自动播放动画
    last_animation_time = pygame.time.get_ticks()
    animation_interval = 3000  # 每3秒播放一次动画

    running = True
    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # 处理鼠标事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    # 检查是否点击了工具按钮
                    pos = event.pos
                    if tool_buttons["pen"].collidepoint(pos):
                        whiteboard.mode = "pen"
                    elif tool_buttons["eraser"].collidepoint(pos):
                        whiteboard.mode = "eraser"
                    elif tool_buttons["undo"].collidepoint(pos):
                        whiteboard.undo()
                    elif tool_buttons["clear"].collidepoint(pos):
                        whiteboard.clear()
                    else:
                        # 开始在白板上绘图
                        whiteboard.start_drawing(pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键释放
                    whiteboard.stop_drawing()

            elif event.type == pygame.MOUSEMOTION:
                # 更新绘图过程
                whiteboard.update_drawing(event.pos)

            # 可选：添加按键事件来手动触发动画
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 空格键触发动画
                    model_v3.StartRandomMotion("TapBody", 3)
                    model_v3_2.StartRandomMotion("TapBody", 3)

        if not running:
            break

        # 定期自动播放随机动作
        if current_time - last_animation_time > animation_interval:
            model_v3.StartRandomMotion("Idle", 1)  # 播放Idle动画
            model_v3_2.StartRandomMotion("Idle", 1)  # 播放Idle动画
            last_animation_time = current_time

        # Clear buffer
        l2d_v3.clearBuffer()

        # 先绘制背景
        draw_pygame_background(pygame.display.get_surface(), background_image)

        # 然后绘制Live2D模型
        model_v3_2.Update()
        model_v3_2.Draw()

        model_v3.Update()
        model_v3.Draw()

        # 最后只绘制白板相关的UI元素，而不是整个屏幕
        draw_whiteboard(whiteboard, display)
        draw_tool_buttons(tool_buttons, whiteboard, font, display)
        draw_mode_indicator(whiteboard, font, display)

        pygame.display.flip()
        clock.tick(60)  # 限制帧率为60 FPS

    l2d_v3.dispose()

    pygame.quit()


if __name__ == "__main__":
    main()
