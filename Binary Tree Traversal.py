import pygame
import sys
import tkinter as tk
from tkinter import simpledialog

pygame.init()
font = pygame.font.Font(None, 30)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

WIDTH, HEIGHT = 1000, 600
SIDE_BAR_WIDTH = 200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visual Binary Tree")

DOUBLE_CLICK_TIME = 0.5

def show_popup(title, message):
    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(text_box.get("1.0", "end-1c"))
        root.update()

    root = tk.Tk()
    root.title(title)
    root.geometry("400x300")

    text_box = tk.Text(root, wrap='word')
    text_box.insert('1.0', message)
    text_box.config(state='disabled')
    text_box.pack(expand=True, fill='both')

    copy_button = tk.Button(root, text="Copy to clipboard", command=copy_to_clipboard)
    copy_button.pack(pady=10)

    root.mainloop()

class Node:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.radius = 30
        self.selected = False
        self.parent = None
        self.left = None
        self.right = None
    
    def draw(self, screen, zoom, offset_x, offset_y):
        color = RED if self.selected else BLUE
        pygame.draw.circle(screen, color, (int(self.x * zoom + offset_x), int(self.y * zoom + offset_y)), int(self.radius * zoom))
        text = font.render(self.name, True, WHITE)
        screen.blit(text, (int(self.x * zoom + offset_x - text.get_width() // 2), int(self.y * zoom + offset_y - text.get_height() // 2)))

    def is_clicked(self, pos, zoom, offset_x, offset_y):
        dx = self.x * zoom + offset_x - pos[0]
        dy = self.y * zoom + offset_y - pos[1]
        return (dx * dx + dy * dy) <= ((self.radius * zoom) * (self.radius * zoom))

class BinaryTree:
    def __init__(self):
        self.root = Node('Root', WIDTH // 2 - SIDE_BAR_WIDTH // 2, 100)
        self.nodes = [self.root]
        self.selected_node = None
        self.spacing_x = 150
        self.spacing_y = 100

    def add_node(self, parent_node, name, is_left):
        if is_left and parent_node.left is not None:
            return
        if not is_left and parent_node.right is not None:
            return

        new_node = Node(name, 0, 0)
        if is_left:
            parent_node.left = new_node
        else:
            parent_node.right = new_node
        new_node.parent = parent_node
        self.nodes.append(new_node)
        self.auto_adjust()

    def remove_node(self, node):
        # Case 1: Node is the root or not on the list
        if node not in self.nodes or node == self.root:
            return  

        # Case 2: Node without children
        if node.left is None and node.right is None:
            if node.parent:
                if node.parent.left == node:
                    node.parent.left = None
                elif node.parent.right == node:
                    node.parent.right = None
            self.nodes.remove(node)

        # Case 3: Node with one child
        elif node.left is None or node.right is None:
            child = node.left if node.left else node.right
            if node.parent:
                if node.parent.left == node:
                    node.parent.left = child
                elif node.parent.right == node:
                    node.parent.right = child
            child.parent = node.parent
            self.nodes.remove(node)

        # Case 4: Node with two children
        else:
            successor = self._find_min(node.right)
            node.name = successor.name
            self.remove_node(successor)

    def _find_min(self, node):
        while node.left:
            node = node.left
        return node

    def select_node(self, pos, zoom, offset_x, offset_y):
        for node in self.nodes:
            if node.is_clicked(pos, zoom, offset_x, offset_y):
                if self.selected_node:
                    self.selected_node.selected = False
                node.selected = True
                self.selected_node = node
                break

    def deselect_node(self):
        if self.selected_node:
            self.selected_node.selected = False
            self.selected_node = None

    def auto_adjust(self):
        def adjust_subtree(node, x, y, depth):
            if node is None:
                return x
            new_x = adjust_subtree(node.left, x, y + self.spacing_y, depth + 1)
            node.x = new_x
            node.y = y
            new_x = adjust_subtree(node.right, new_x + self.spacing_x, y + self.spacing_y, depth + 1)
            return new_x

        adjust_subtree(self.root, WIDTH // 2 - SIDE_BAR_WIDTH // 2, 100, 0)

    def draw(self, screen, zoom, offset_x, offset_y):
        screen.fill(WHITE)
        for node in self.nodes:
            if node.parent:
                pygame.draw.line(screen, BLACK, 
                                 (int(node.x * zoom + offset_x), int(node.y * zoom + offset_y)),
                                 (int(node.parent.x * zoom + offset_x), int(node.parent.y * zoom + offset_y)), 2)
        for node in self.nodes:
            node.draw(screen, zoom, offset_x, offset_y)

    # Binary tree traversal methods
    def inorder(self, node, result=None):
        if result is None:
            result = []
        if node.left:
            self.inorder(node.left, result)
        result.append(node.name)
        if node.right:
            self.inorder(node.right, result)
        return result

    def preorder(self, node, result=None):
        if result is None:
            result = []
        result.append(node.name)
        if node.left:
            self.preorder(node.left, result)
        if node.right:
            self.preorder(node.right, result)
        return result

    def postorder(self, node, result=None):
        if result is None:
            result = []
        if node.left:
            self.postorder(node.left, result)
        if node.right:
            self.postorder(node.right, result)
        result.append(node.name)
        return result

def show_edit_name_dialog(node):
    root = tk.Tk()
    root.withdraw()
    new_name = simpledialog.askstring("Edit node name", "New name:", initialvalue=node.name)
    if new_name:
        node.name = new_name
    root.quit()

def draw_sidebar(screen):
    sidebar_rect = pygame.Rect(WIDTH - SIDE_BAR_WIDTH, 0, SIDE_BAR_WIDTH, HEIGHT)
    pygame.draw.rect(screen, GRAY, sidebar_rect)

    buttons = [
        {"text": "Add Left", "pos": (WIDTH - 200, 50), "action": "add_left"},
        {"text": "Add Right", "pos": (WIDTH - 200, 100), "action": "add_right"},
        {"text": "Delete Node", "pos": (WIDTH - 200, 150), "action": "delete_node"},
        {"text": "Calc Inorder", "pos": (WIDTH - 200, 200), "action": "inorder"},
        {"text": "Calc Preorder", "pos": (WIDTH - 200, 250), "action": "preorder"},
        {"text": "Calc Postorder", "pos": (WIDTH - 200, 300), "action": "postorder"}
    ]

    for button in buttons:
        pygame.draw.rect(screen, BLACK, (button["pos"][0], button["pos"][1], 160, 40), 2)
        text = font.render(button["text"], True, BLACK)
        screen.blit(text, (button["pos"][0] + 10, button["pos"][1] + 10))
    
    return buttons

def check_button_click(pos, buttons, tree):
    for button in buttons:
        if button["pos"][0] <= pos[0] <= button["pos"][0] + 160 and button["pos"][1] <= pos[1] <= button["pos"][1] + 40:
            if button["action"] == "inorder":
                result = "Inorder: " + ", ".join(tree.inorder(tree.root))
                show_popup("Inorder Traversal", result)
            elif button["action"] == "preorder":
                result = "Preorder: " + ", ".join(tree.preorder(tree.root))
                show_popup("Preorder Traversal", result)
            elif button["action"] == "postorder":
                result = "Postorder: " + ", ".join(tree.postorder(tree.root))
                show_popup("Postorder Traversal", result)
            elif button["action"] == "add_left" or button["action"] == "add_right":
                if tree.selected_node:
                    name = simpledialog.askstring("Add Node", "New Node Name:")
                    if name:
                        tree.add_node(tree.selected_node, name, button["action"] == "add_left")
            elif button["action"] == "delete_node":
                if tree.selected_node:
                    tree.remove_node(tree.selected_node)
                    tree.deselect_node()

def main():
    clock = pygame.time.Clock()
    tree = BinaryTree()
    zoom = 1
    offset_x, offset_y = 0, 0
    last_click_time = 0
    dragging = False
    last_mouse_pos = None
    buttons = draw_sidebar(screen)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pygame.time.get_ticks() - last_click_time < DOUBLE_CLICK_TIME * 1000:
                        if tree.selected_node:
                            show_edit_name_dialog(tree.selected_node)
                    else:
                        last_click_time = pygame.time.get_ticks()
                        tree.select_node(event.pos, zoom, offset_x, offset_y)
                        check_button_click(event.pos, buttons, tree)
                elif event.button == 2:
                    dragging = True
                    last_mouse_pos = event.pos
                elif event.button == 4:
                    zoom *= 1.1
                elif event.button == 5:
                    zoom /= 1.1
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    dragging = False
                    last_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging and last_mouse_pos:
                    offset_x += event.pos[0] - last_mouse_pos[0]
                    offset_y += event.pos[1] - last_mouse_pos[1]
                    last_mouse_pos = event.pos

        screen.fill(WHITE)
        tree.draw(screen, zoom, offset_x, offset_y)
        buttons = draw_sidebar(screen)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
